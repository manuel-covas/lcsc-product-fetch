import sys
import asyncio
import time
import requests
import json
from alive_progress import alive_bar

def print_usage():
    print("Usage:\n")
    print("  {} <file | inline> <path | product_code[,product_code...]>".format(sys.argv[0]))
    print("\nArguments:\n")
    print("  mode: mode to operate in, either 'file' or 'inline'")
    print("  path: path to a file containing the product codes to fetch.")
    print("  product_code: one or more product codes.")
    print("\nProduct code format:\n")
    print("  In both modes, LCSC product codes should be provided as such:")
    print("    C######,C######,C######...")
    print("\nModes of operation:\n")
    print("  'file':")
    print("    In this mode the product codes in the file at 'path' will")
    print("    be fetched and the output will be saved to <path>'.csv'\n")
    print("  'inline':")
    print("    In this mode, the product codes in the 'product_codes' argument")
    print("    will be fetched and the output will be saved to 'output.csv'\n")
    exit()

if len(sys.argv) < 3:
    print("Missing arguments.\n")
    print_usage()


# Parse arguments

opertion_mode = sys.argv[1]
product_codes = []

if opertion_mode == "file":
    product_codes = open(sys.argv[2], "r").read().split(",")

elif opertion_mode == "inline":
    product_codes = sys.argv[2].split(",")

else:
    print("Invalid mode '{}'\n".format(opertion_mode))
    print_usage()


# Looks up a product code.

def lookup_product_code(product_code, progress_bar):
    try:
        response: dict = requests.get(
            f"https://wmsc.lcsc.com/ftps/wm/product/detail?productCode={product_code}",
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            }
        ).json()

        if response["result"] != None:
            result: dict = response["result"]
            progress_bar()
            return {
                "success": True, 
                "product_code": product_code,
                "product_details": {
                    "manufacturer":             result.get("brandNameEn"),
                    "manufacturer_part_number": result.get("productModel"),
                    "lcsc_product_code":        product_code,
                    "package":                  result.get("encapStandard"),
                    "product_description":      result.get("productIntroEn"),
                    "amount_in_stock":          result.get("stockNumber"),
                    "product_page":             f"https://www.lcsc.com/product-detail/{product_code}.html"
                }
            }

    except:
        pass
    progress_bar()
    return {
        "success": False,
        "product_code": product_code
    }


# Asynchronous product lookup

async def lookup_product_codes():

    event_loop = asyncio.get_running_loop()
    co_routines = []
    valid_products = []
    dropped_products = []

    # Proceed to looking up loaded product codes.
    with alive_bar(len(product_codes), "Looking up product codes...") as progress_bar:

        # Start asynchronous lookups
        for product_code in product_codes:
            co_routines.append(event_loop.run_in_executor(None, lookup_product_code, product_code, progress_bar))
            time.sleep(.1)

        # Process results
        for co_routine in co_routines:
            result = await co_routine

            if result["success"]:
                valid_products.append(result)
            else:
                dropped_products.append(result)

    return {
        "valid_products": valid_products,
        "dropped_products": dropped_products
    }


# Lookup product codes

lookup_result = asyncio.run(lookup_product_codes())
valid_results = lookup_result["valid_products"]
dropped_results = lookup_result["dropped_products"]

if len(valid_results) == 0:
    print("No products were found.")
    exit()

print("Found {} out of {} products.".format(len(valid_results), len(product_codes)))

if len(dropped_results) > 0:
    print("Dropping the following product codes:")
for result in dropped_results:
    print("  - {}".format(result["product_code"]))


output_csv = "LCSC Product Code,Amount in Stock,Package,Manufacturer,Manufacturer Part Number,Product Description,Product Page"

for result in valid_results:
    product_details = result["product_details"]

    output_csv += '\n"{}","{}","{}","{}","{}","{}","{}"'.format(
        product_details["lcsc_product_code"],
        product_details["amount_in_stock"],
        product_details["package"],
        product_details["manufacturer"],
        product_details["manufacturer_part_number"],
        product_details["product_description"],
        product_details["product_page"]
    )

if opertion_mode == "file":
    open(sys.argv[2]+".csv", "w").write(output_csv)
    print("Output written to "+sys.argv[2]+".csv")
elif opertion_mode == "inline":
    open("output.csv", "w").write(output_csv)
    print("Output written to output.csv")