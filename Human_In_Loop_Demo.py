from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from typing import TypedDict

class State(TypedDict):
    amount: float
    status: str

def request_approval(State):
    print('Request Approval Process. Amount:'+ str(State['amount']))
    if State['amount']>750:
        return {"status":"pending_approval"}
    return {"status":"auto_approved"}

def finalize(State) -> State:
    print('Finalize Process')
    State['status']='Manual Approval'
    return State 
    #{"status":"finalized Status" + State['status']}

if __name__ == "__main__":
    amtValue=1500
    graph=StateGraph(State)
    graph.add_node("request_approval",request_approval)
    graph.add_node("finalize", finalize)
    graph.set_entry_point("request_approval")
    
    graph.add_edge("request_approval", "finalize")
    graph.add_edge("finalize", END)
    
    app = graph.compile(checkpointer=MemorySaver(), interrupt_before=["finalize"])
    config = {"configurable": {"thread_id":"thread_1"}}
    app.invoke({"amount":amtValue, "status":""}, config)

    decision=input("Approve $" + str(amtValue) + "?(yes/No):")
    if decision=="yes":
        result=app.invoke(None, config)
        print(result.get('status'))
        
