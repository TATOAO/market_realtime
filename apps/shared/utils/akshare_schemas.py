from ..schemas.ashare_stock import AShareStockRecord, AShareStockFilter

def filter_records(records: list[AShareStockRecord], filters: AShareStockFilter) -> list[AShareStockRecord]:
    """Filter records based on specified criteria"""
    filtered_records = records
    
    if filters.codes:
        filtered_records = [r for r in filtered_records if r.code in filters.codes]
    
    if filters.min_change_percent is not None:
        filtered_records = [r for r in filtered_records if r.change_percent >= filters.min_change_percent]
    
    if filters.max_change_percent is not None:
        filtered_records = [r for r in filtered_records if r.change_percent <= filters.max_change_percent]
    
    if filters.min_volume is not None:
        filtered_records = [r for r in filtered_records if r.volume >= filters.min_volume]
    
    if filters.min_turnover is not None:
        filtered_records = [r for r in filtered_records if r.turnover >= filters.min_turnover]
    
    if filters.min_pe_ratio is not None:
        filtered_records = [r for r in filtered_records if r.pe_ratio >= filters.min_pe_ratio]
    
    if filters.max_pe_ratio is not None:
        filtered_records = [r for r in filtered_records if r.pe_ratio <= filters.max_pe_ratio]
    
    if filters.min_pb_ratio is not None:
        filtered_records = [r for r in filtered_records if r.pb_ratio >= filters.min_pb_ratio]
    
    if filters.max_pb_ratio is not None:
        filtered_records = [r for r in filtered_records if r.pb_ratio <= filters.max_pb_ratio]
    
    # Apply limit
    if filters.limit:
        filtered_records = filtered_records[:filters.limit]
    
    return filtered_records 