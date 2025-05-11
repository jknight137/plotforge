import argparse
from cli import (
    create_project,
    generate_outline,
    generate_chapter,
    manage_models
)

def main():
    parser = argparse.ArgumentParser(description="PlotForge CLI - Local Fiction Writing Assistant")
    subparsers = parser.add_subparsers(dest="command")

    # create new project
    parser_new = subparsers.add_parser("new", help="Create a new writing project")
    parser_new.add_argument("name", help="Project name")

    # generate outline
    parser_outline = subparsers.add_parser("outline", help="Generate or import an outline")
    parser_outline.add_argument("name", help="Project name")
    parser_outline.add_argument("--model", help="Override model for this generation")
    parser_outline.add_argument("--from-file", help="Path to a manually written outline")

    # generate chapter
    parser_chapter = subparsers.add_parser("generate-chapter", help="Generate a chapter draft")
    parser_chapter.add_argument("name", help="Project name")
    parser_chapter.add_argument("--number", type=int, required=True, help="Chapter number (e.g., 1)")
    parser_chapter.add_argument("--model", help="Override model")

    # model management
    parser_models = subparsers.add_parser("models", help="Manage models for a project")
    parser_models.add_argument("name", help="Project name")
    parser_models.add_argument("--list", action="store_true", help="List available models")
    parser_models.add_argument("--set", dest="set_primary", help="Set primary model")

    args = parser.parse_args()

    if args.command == "new":
        create_project(args.name)

    elif args.command == "outline":
        generate_outline(args.name, model_override=args.model, from_file=args.from_file)

    elif args.command == "generate-chapter":
        generate_chapter(args.name, args.number, model_override=args.model)

    elif args.command == "models":
        manage_models(args.name, list_flag=args.list, set_primary=args.set_primary)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
