from models.stock import StockModel

def find_matches(search_input):
    stocks_in_db = StockModel.objects.only('ticker', 'full_name').order_by('full_name')

    search_input = search_input.lower()

    name_matches = []
    ticker_matches = []

    for stock in stocks_in_db:
        stock_json = {'full_name': stock.full_name, 'ticker': stock.ticker.upper()}            
        if stock.full_name.lower().startswith(search_input):                
            name_matches.append(stock_json)
        if len(name_matches) >= 10:
            break

    for stock in stocks_in_db:
        stock_json = {'full_name': stock.full_name, 'ticker': stock.ticker.upper()}            
        if stock.ticker.lower().startswith(search_input):                
            ticker_matches.append(stock_json)
        if len(ticker_matches) >= 8:
            break

    recommended_list = []

    for stock in ticker_matches:
        if name_matches.count(stock) > 0:
            name_matches.remove(stock)

    if len(name_matches) >= len(ticker_matches):
        quantity = min(len(ticker_matches), 4)
        for i in range(min((8-quantity), len(name_matches))):
            recommended_list.append(name_matches[i])
        for i in range(quantity):
            recommended_list.append(ticker_matches[i])
    elif len(name_matches) < len(ticker_matches):
        quantity = min(len(name_matches), 4)
        for i in range(quantity):
            recommended_list.append(name_matches[i])
        for i in range(min((8-quantity), len(ticker_matches))):
            recommended_list.append(ticker_matches[i])


    if len(recommended_list) < 8:
        for stock in stocks_in_db:
            stock_json = {'full_name': stock.full_name, 'ticker': stock.ticker.upper()}
            if stock.full_name.lower().find(search_input) > 0 and recommended_list.count(stock_json) == 0:
                recommended_list.append(stock_json)
            if len(recommended_list) >= 8:
                break


    return recommended_list