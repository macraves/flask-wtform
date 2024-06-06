"""List of promotions functions"""

import ioput as io
from products_promotion import PercentageDiscount, SecondHalfPrice, ThirdOneFree
from store import test_remove_product


class NoPromitionValue(Exception):
    """To stop Inner loop"""

    def __init__(self, message) -> None:
        super().__init__(message)


def get_template():
    """Return menu desing"""
    inner_menu = """{line}
{title}
{items}
{line}"""
    return inner_menu


def promotion_managment(chosen_product) -> object:  # Promotion object
    """According the user choice create Promotion instance 
    Instance's properties are provided by user
    Returns:
        object: Promotion type instance gets assigned to property of: product.promotion
    """

    if chosen_product.promotion is None:
        promotion_options = {
            1: PercentageDiscount,
            2: SecondHalfPrice,
            3: ThirdOneFree
        }

        promotion_map = map(lambda double: f"{double[0]}: {str(double[1].__name__)}", enumerate(
            promotion_options.values(), start=1))
        promotion_template = "\n".join(promotion_map)

        promotion = io.read_int_ranged(
            promotion_template + "\n\nEnter the promotion no: ",
            min_value=1, max_value=len(promotion_options))
        if promotion == 1:
            ratio = io.read_float("Discount percentange: ")
            return promotion_options[promotion](ratio)
        if promotion == 2:
            step_for_half_price = 2
            return promotion_options[promotion](step_for_half_price)
        if promotion == 3:
            step_to_free = 3
            return promotion_options[promotion](step_to_free)
    else:
        if io.ask_to_continue(
                f"""Product info:
            {chosen_product} 
            It has already been promoted
            Do you want to delete it y/n? """):
            # assigns None to produc.promotion property
            chosen_product.promotion = None
        else:
            # if user decided to keep current promotion it will return it back
            return chosen_product.promotion


def remove_management(product):
    """to not change all convention"""
    if product.promotion is None:
        raise NoPromitionValue(
            "The product does not have any promotion to remove")
    product.promotion = None

    return product.promotion


def product_list_iner_loop(shop: object, function, menu_title, action):
    """That will execute function method as user requested"""
    while True:
        add_menu = get_template().format(
            line="*"*len(menu_title), title=menu_title, items=shop)
        product_no = io.read_int_ranged(
            f"{add_menu}\nSelect a product to {action} a promotion: ",
            min_value=1, max_value=len(shop.stock))
        # product variable is assigned products.Product object by user entry
        product = shop.stock[product_no-1]
        # promotion property gets its value as Promotion type
        try:
            product.promotion = function(product)
        except NoPromitionValue as npv:
            print(f"{npv}".upper())
            break
        if not io.ask_to_continue(f"Do you want to {action} another promotion y/n? "):
            break


def add_promotion(shop: object):
    """Opens up menu to display product list of store
    User enters product no to add promotion to Product
    Chosen Product.promotion attributes invokes and  get assigen
    with Promotion instance"""
    menu_title = "PROMOTION MANAGMENT"
    action_name = "ADD"
    product_list_iner_loop(shop, promotion_managment, menu_title, action_name)


def show_product_details(shop):
    """iterate through in shop.stock list to find the product by name"""
    search_result = None
    product_name = io.read_text("Please enter the product name: ")
    product_name = product_name.strip().title()
    for product in shop.stock:
        if product_name in product.name:
            search_result = product
    if search_result is not None:
        print(f"\nFound Product according your entry:\n{search_result}\n")
    else:
        print(f"\n{product_name} is not found in the stock\n")


def remove_promotion(shop: object) -> None:
    """This method has been already in promotion managment
    as the project ask for this method add promotion inner loop will be another method"""
    action_name = "REMOVE"
    remove_title = "REMOVE PROMOTION"
    product_list_iner_loop(shop, remove_management, remove_title, action_name)


def validate_user_answer():
    """Returns list of lists, nested list first index is product index
    nested list second index amount to buy
    Ignores non integer base entries
    """
    questions = ["Which product # do you want? ", "What amount do you want? "]
    basket = []
    while True:
        answers = []
        for question in questions:
            answer = input(question)
            if answer.isnumeric():
                answer = int(answer)
            answers.append(answer)
        # Eliminate non integer entry
        is_any_not_int = any(not isinstance(item, int) for item in answers)
        if is_any_not_int:
            break
        basket.append(answers)
    return basket


def comparison_of_products(shop):
    "PPRICE COMPARSION"
    func_title = "PPRICE COMPARSION"
    items_menu = get_template()
    all_products_str = "\n".join(
        f"{i}.{product}" for i, product in enumerate(shop.stock, start=1))
    items_menu.format(line="*"*len(func_title),
                      title=func_title, items=all_products_str)
    first_product = io.read_int_ranged(all_products_str +
                                       "\nChose your first product: ", min_value=1, max_value=len(shop.stock))
    second_product = io.read_int_ranged(
        "Chose your second product: ", min_value=1, max_value=len(shop.stock))
    products = [shop.stock[first_product-1].price,
                shop.stock[second_product-1].price]

    return f"Expensive product is: {max(products)}\nCheapest product is {min(products)}"


def instance_logic_methods(shop):
    """Comparasin, sorting"""
    max_price = max(product.price for product in shop.stock)
    min_price = min(product.price for product in shop.stock)
    high_price_to_lowest = sorted(
        shop.stock, key=lambda item: item.price, reverse=True)
    hig_low_text = "\n".join(
        f"{i}.{item}" for i, item in enumerate(high_price_to_lowest, start=1))
    # TypeError: '<' not supported between instances of 'Product' and 'Product'
    # lowest_to_highest = sorted(high_price_to_lowest) """Aborted"""
    lowest_to_highest = sorted(shop.stock, key=lambda x: x.price)
    low_to_high_text = "\n".join(
        f"{i}.{x}" for i, x in enumerate(lowest_to_highest, start=1))
    # print(hig_low_text)
    # print(low_to_high_text)
    user_menu = {

        1: "Max price in the stock",
        2: "Min price in the stock",
        3: "Sort highest to lowest",
        4: "Sort lowest to highest",
        5: "Compare two product price"
    }
    user_menu_str = "\n".join(
        map(lambda x: f"{x[0]}: {str(x[1])}", user_menu.items()))
    while True:
        command = io.read_int_ranged(
            user_menu_str+"\nWhat is your command: ", min_value=1, max_value=len(user_menu))
        if command == 1:
            print(max_price)
        elif command == 2:
            print(min_price)
        elif command == 3:
            print(hig_low_text)
        elif command == 4:
            print(low_to_high_text)
        elif command == 5:
            print(comparison_of_products(shop))
        if io.ask_to_continue("To continue press any button but stop 'y'..."):
            break
