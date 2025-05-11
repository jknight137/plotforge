import argparse
from cli import create_project, generate_chapter, generate_page, manage_models

def main():
    parser = argparse.ArgumentParser(description="PlotForge CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Create new project
    subparsers.add_parser("new").add_argument("name")

    # Generate chapter
    ch_parser = subparsers.add_parser("generate-chapter")
    ch_parser.add_argument("name")
    ch_parser.add_argument("--number", type=int, required=True)
    ch_parser.add_argument("--model")
    ch_parser.add_argument("--test-models", action="store_true")

    # Generate page (500 words)
    pg_parser = subparsers.add_parser("generate-page")
    pg_parser.add_argument("name")
    pg_parser.add_argument("--number", type=int, required=True)
    pg_parser.add_argument("--model")
    pg_parser.add_argument("--test-models", action="store_true")

    # Manage models
    models_parser = subparsers.add_parser("models")
    models_parser.add_argument("name")
    models_parser.add_argument("--list", action="store_true")
    models_parser.add_argument("--set", dest="set_primary", help="Set primary model")

    args = parser.parse_args()

    if args.command == "new":
        create_project(args.name)
    elif args.command == "generate-chapter":
        generate_chapter(args.name, args.number, args.model, args.test_models)
    elif args.command == "generate-page":
        generate_page(args.name, args.number, args.model, args.test_models)
    elif args.command == "models":
        manage_models(args.name, list_flag=args.list, set_primary=args.set_primary)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
