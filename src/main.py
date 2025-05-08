import argparse
from cli import create_project, generate_outline

def main():
    parser = argparse.ArgumentParser(description="AI Fiction Writing Assistant")
    subparsers = parser.add_subparsers(dest="command")

    parser_new = subparsers.add_parser("new", help="Create a new writing project")
    parser_new.add_argument("name", help="Project name")

    parser_outline = subparsers.add_parser("outline", help="Generate an outline for the project")
    parser_outline.add_argument("name", help="Project name")

    args = parser.parse_args()

    if args.command == "new":
        create_project(args.name)
    elif args.command == "outline":
        generate_outline(args.name)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
