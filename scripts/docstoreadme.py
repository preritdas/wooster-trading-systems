import os


current_dir = os.path.dirname(os.path.realpath(__file__))
doc_loc = os.path.join(current_dir, "..", "cliref.md")
readme_loc = os.path.join(current_dir, "..", "README.md")


def read_contents() -> tuple[list[str], list[str]]:
    """
    Contents of the doc and readme files.
    """
    with open(doc_loc, "r", encoding="utf-8") as f:
        doc_contents = f.readlines()

    with open(readme_loc, "r", encoding="utf-8") as f:
        readme_contents = f.readlines()

    return doc_contents, readme_contents


def write_readme(readme_contents: list[str], doc_contents: list[str]) -> None:
    """
    Writes the new readme.
    """
    readme_contents.extend(doc_contents)

    with open(readme_loc, "w", encoding="utf-8") as f:
        f.writelines(readme_contents)


def main():
    doc_contents, readme_contents = read_contents()
    
    # Change the reference header 1
    doc_contents[0] = "# CLI Reference - `wooster`"

    # Update the contents
    old_ref_loc = readme_contents.index("# CLI Reference - `wooster`\n")
    readme_contents = readme_contents[:old_ref_loc]

    # Write the results
    write_readme(readme_contents, doc_contents)

    
if __name__ == '__main__':
    main()
