def query_check(query:str):
    query = query.upper()
    if "DELETE" in query:
        if not "WHERE" in query:
            raise "SQL Query ERROR : DELETE문은 WHERE문과 함께 사용되어야 합니다."
    return query