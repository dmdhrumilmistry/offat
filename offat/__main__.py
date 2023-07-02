from argparse import ArgumentParser
from .openapi import OpenAPIParser


if __name__ == '__main__':
    parser = ArgumentParser(prog='offat')
    parser.add_argument('-f','--file', dest='fpath', type=str, help='path of openapi/swagger specification file', required=True)
    
    args = parser.parse_args()

    api_doc = OpenAPIParser(args.fpath)
    print(api_doc.base_url)
