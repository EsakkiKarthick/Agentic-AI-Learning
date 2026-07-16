import pdfplumber
import re
from langgraph import StateGraph, END
from langgraph.types import interrupt, Command
from typing import TypedDict, Annotated, Optional
import operator

class expenseState():
    pdf_path: str
    input_data: str
    invoice_no: str
    unique_id: str
    amount: float
    risk_score: int
    status: str
    manual_decision: str

def extract_data(state: expenseState)-> expenseState:
    inputFilePath=state.get('pdf_path','')
    if inputFilePath:
        with pdfplumber.open(inputFilePath) as pdf:
            invoice_data=pdf.pages[0].extract_text()
        if invoice_data:
            invoice_no= re.search(r"Invoice\s*(?:No\.?|Number)[:\s]*([A-Za-z0-9\-\/]+)", invoice_data)
            total_amount=re.search(r"Total\s*(?:Amount)?[:\s]*([\d,]+\.\d{2})", invoice_data)
            print(f'Invoice Number:{invoice_no} Total Amount:{total_amount}')
            state['invoice_no']=invoice_no
            state['amount']=total_amount
    else:
        print('PDF data not exists. Proceed to LLM call')
    return state

def validate_amount(state: expenseState)-> str:
    if state['amount']>THRESHOLD_AMOUNT:
        return "auto_approval"
    else:
        return "manual_approval"
    
def auto_approve(state: expenseState)-> expenseState:
    invoice_no = state.get('invoice_no','')
    invoice_amount = state.get('amount',0)
    state['status']='Auto Approved'
    print(f"Auto Approved. Invoice No:{invoice_no}. Invoice Amount:{invoice_amount}")
    return state

def manual_approve(state: expenseState) -> expenseState:
    decision = interrupt({
        "message": "Approval Required",
        "invoice_no": state['invoice_no'],
        "invoice_amount": state['amount']
    })
    return {"manual_decision": decision['decision']}

def read_response(state: expenseState) -> expenseState:
    if state.get('manual_decision','')=='Approved':
        print('Manual Approval')
    else:
        print('Rejected')
    return state
    
if __name__ == '__main__':
    THRESHOLD_AMOUNT=5000
    graph= StateGraph(expenseState)

    graph.add_node("extract_node", extract_data)
    graph.add_node("validation_node", validate_amount)
    graph.add_node("autoApprove_node", auto_approve)
    graph.add_node("manualApprove_node", manual_approve)
    graph.add_node("read_response", read_response)
    
    graph.set_entry_point("extract_node")
    graph.add_edge("extract_node", "validation_node")
    graph.add_conditional_edge("validation_node", {
        "auto_approval" : "autoApprove_node",
        "manual_approval" : "manualApprove_node"
    })
    graph.add_edge("autoApprove_node", END)
    graph.add_edge("manualApprove_node", END)
    app = graph.compile()

