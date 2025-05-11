import argparse
from cli import (
    create_project,
    generate_chapter,
    generate_page,
    manage_models,
    generate_outline,
    approve_outline,
    approve_page,
    reject_page,
    approve_chapter,
    write_chapter,
    project_status,
    concat_chapter,
    summarize_chapter,
    reject_chapter
)

def main():
    parser = argparse.ArgumentParser(description="PlotForge CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("new").add_argument("name")

    ch_parser = subparsers.add_parser("generate-chapter")
    ch_parser.add_argument("name")
    ch_parser.add_argument("--number", type=int, required=True)
    ch_parser.add_argument("--model")
    ch_parser.add_argument("--test-models", action="store_true")

    concat_parser = subparsers.add_parser("concat-chapter")
    concat_parser.add_argument("name")
    concat_parser.add_argument("--number", type=int, required=True)
    concat_parser.add_argument("--pages", type=int, default=10)

    write_ch_parser = subparsers.add_parser("write-chapter")
    write_ch_parser.add_argument("name")
    write_ch_parser.add_argument("--number", type=int, required=True)
    write_ch_parser.add_argument("--pages", type=int, default=10)
    write_ch_parser.add_argument("--model")

    pg_parser = subparsers.add_parser("generate-page")
    pg_parser.add_argument("name")
    pg_parser.add_argument("--number", type=int, required=True)
    pg_parser.add_argument("--model")
    pg_parser.add_argument("--test-models", action="store_true")

    models_parser = subparsers.add_parser("models")
    models_parser.add_argument("name")
    models_parser.add_argument("--list", action="store_true")
    models_parser.add_argument("--set", dest="set_primary")

    outline_parser = subparsers.add_parser("generate-outline")
    outline_parser.add_argument("name")
    outline_parser.add_argument("--model")

    approve_parser = subparsers.add_parser("approve-outline")
    approve_parser.add_argument("name")

    approve_page_parser = subparsers.add_parser("approve-page")
    approve_page_parser.add_argument("name")
    approve_page_parser.add_argument("--number", type=int, required=True)

    reject_page_parser = subparsers.add_parser("reject-page")
    reject_page_parser.add_argument("name")
    reject_page_parser.add_argument("--number", type=int, required=True)
    reject_page_parser.add_argument("--reason", default="")

    approve_chapter_parser = subparsers.add_parser("approve-chapter")
    approve_chapter_parser.add_argument("name")
    approve_chapter_parser.add_argument("--number", type=int, required=True)
    approve_chapter_parser.add_argument("--pages", type=int, default=10)


    reject_chapter_parser = subparsers.add_parser("reject-chapter")
    reject_chapter_parser.add_argument("name")
    reject_chapter_parser.add_argument("--number", type=int, required=True)
    reject_chapter_parser.add_argument("--reason", default="")

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("name")

    summarize_ch_parser = subparsers.add_parser("summarize-chapter")
    summarize_ch_parser.add_argument("name")
    summarize_ch_parser.add_argument("--number", type=int, required=True)
    summarize_ch_parser.add_argument("--model")


    args = parser.parse_args()

    if args.command == "new":
        create_project(args.name)
    elif args.command == "generate-chapter":
        generate_chapter(args.name, args.number, args.model, args.test_models)
    elif args.command == "generate-page":
        generate_page(args.name, args.number, args.model, args.test_models)
    elif args.command == "models":
        manage_models(args.name, list_flag=args.list, set_primary=args.set_primary)
    elif args.command == "generate-outline":
        generate_outline(args.name, args.model)
    elif args.command == "approve-outline":
        approve_outline(args.name)
    elif args.command == "approve-page":
        approve_page(args.name, args.number)
    elif args.command == "reject-page":
        reject_page(args.name, args.number, args.reason)
    elif args.command == "approve-chapter":
        approve_chapter(args.name, args.number)
    elif args.command == "reject-chapter":
        reject_chapter(args.name, args.number, args.reason)
    elif args.command == "write-chapter":
        write_chapter(args.name, args.number, args.pages, args.model)
    elif args.command == "concat-chapter":
        concat_chapter(args.name, args.number, args.pages)
    elif args.command == "status":
        project_status(args.name)
    elif args.command == "summarize-chapter":
        summarize_chapter(args.name, args.number, args.model)
    elif args.command == "approve-chapter":
        approve_chapter(args.name, args.number, args.pages)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
