from os import listdir, remove, path

# Define a function to parse price
def parse_price(price):
    # Return only digits, no separators or currency symbols
    return "".join(filter(lambda x: x.isdigit() or x == "-", price))


def most_used_categories(n, db_session, Expense):
    categories = db_session.query(Expense.category).all()
    categories = [category[0] for category in categories]
    categories = list(set(categories))
    usages = [categories.count(category) for category in categories]
    sorted_categories = [category for _, category in sorted(zip(usages, categories))]
    return sorted_categories[-n:]



def invalidate_old_sessions():
    session_dir = "flask_session"
    for session_file in listdir(session_dir):
        remove(path.join(session_dir, session_file))