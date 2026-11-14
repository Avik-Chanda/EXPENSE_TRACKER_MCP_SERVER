from fastmcp import FastMCP
import random
import json

mcp = FastMCP("Simple Calculator Server")

@mcp.tool
def add(a: float, b: float):
    """ ADD two given numbers """

    return a+b

@mcp.tool
def random_number(min_val: int= 1 , max_value: int = 100) -> int:
    """ Generate some random numbers between the given min and max value """
    return random.randint(min_val, max_value)

@mcp.resource("info://server")
def server_info() -> str:
    """ Get information about the server """
    info = {
        "name": "Simple calculator server",
        "version": "1.0.0",
        "description": "Simple calculator MCp server",
        "tools": ["add", "random_number"],
        "author": "Avik Chanda"
    }
    return json.dumps(info)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
