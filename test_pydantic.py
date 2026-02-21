from pydantic import BaseModel, Field

class TestSchema(BaseModel):
    req_ph: bool = Field(False)

print("1 ->", TestSchema(req_ph='1').req_ph)
print("0 ->", TestSchema(req_ph='0').req_ph)
print("true ->", TestSchema(req_ph='true').req_ph)
print("false ->", TestSchema(req_ph='false').req_ph)
print("True ->", TestSchema(req_ph='True').req_ph)
print("False ->", TestSchema(req_ph='False').req_ph)
