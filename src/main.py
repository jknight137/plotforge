import argparse
from cli import (
    write_chapter,
    generate_page,
    approve_chapter,
    summarize_chapter,
    generate_outline,
    approve_outline,
    create_project,
    manage_models,
)

def main():
    parser = argparse.ArgumentParser(description="PlotForge CLI")
    subparsers = parser.add_subparsers(dest="command")

    # New project
    subparsers.add_parser("new").add_argument("name")

    # Outline
    outline_parser = subparsers.add_parser("generate-outline")
    outline_parser.add_argument("name")
    outline_parser.add_argument("--model")

    subparsers.add_parser("approve-outline").add_argument("name")

    # Write chapter (full generation)
    write_parser = subparsers.add_parser("write-chapter")
    write_parser.add_argument("name")
    write_parser.add_argument("--number", type=int, required=True)
    write_parser.add_argument("--pages", type=int, default=10)
    write_parser.add_argument("--model")

    # Generate a single page
    gen_page_parser = subparsers.add_parser("generate-page")
    gen_page_parser.add_argument("name")
    gen_page_parser.add_argument("--number", type=int, required=True)
    gen_page_parser.add_argument("--model")
    gen_page_parser.add_argument("--pages", type=int, default=10)

    # Approve a chapter
    approve_parser = subparsers.add_parser("approve-chapter")
    approve_parser.add_argument("name")
    approve_parser.add_argument("--number", type=int, required=True)
    approve_parser.add_argument("--pages", type=int, default=10)

    # Summarize a chapter
    summarize_parser = subparsers.add_parser("summarize-chapter")
    summarize_parser.add_argument("name")
    summarize_parser.add_argument("--number", type=int, required=True)
    summarize_parser.add_argument("--model")

    # Model management
    models_parser = subparsers.add_parser("models")
    models_parser.add_argument("name")
    models_parser.add_argument("--list", action="store_true")
    models_parser.add_argument("--set", dest="set_primary")

    args = parser.parse_args()

    if args.command == "new":
        create_project(args.name)
    elif args.command == "generate-outline":
        generate_outline(args.name, args.model)
    elif args.command == "approve-outline":
        approve_outline(args.name)
    elif args.command == "write-chapter":
        write_chapter(args.name, args.number, total_pages=args.pages, model_override=args.model, pages_per_chapter=args.pages)
    elif args.command == "generate-page":
        generate_page(args.name, args.number, model_override=args.model, pages_per_chapter=args.pages)
    elif args.command == "approve-chapter":
        approve_chapter(args.name, args.number, pages_per_chapter=args.pages)
    elif args.command == "summarize-chapter":
        summarize_chapter(args.name, args.number, args.model)
    elif args.command == "models":
        manage_models(args.name, list_flag=args.list, set_primary=args.set_primary)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
