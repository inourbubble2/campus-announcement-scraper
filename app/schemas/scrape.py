from pydantic import BaseModel
from datetime import date

class DateRangeRequest(BaseModel):
    start_page: int = 1
    start_date: date
    end_date: date
