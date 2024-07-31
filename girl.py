import os
import base64
from pathlib import Path
from markdown2 import markdown

def read_file(filepath):
    """Read the content of a file and return it."""
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

def encode_base64(filepath):
    """Encode file content to base64 for display."""
    with open(filepath, 'rb') as file:
        return base64.b64encode(file.read()).decode('utf-8')

def render_markdown(content):
    return markdown(content)

def generate_tree_html(path, base_path):
    tree_html = "<ul>"
    for item in sorted(Path(path).iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        if item.name == '.git':
            continue  # Skip the .git directory
        rel_path = os.path.relpath(item, base_path)
        if item.is_dir():
            tree_html += f"<li><strong>{item.name}/</strong>{generate_tree_html(item, base_path)}</li>"
        else:
            tree_html += f"<li>{item.name}</li>"
    tree_html += "</ul>"
    return tree_html


def generate_html(info_dict):
    try:
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>GIRL</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" type="text/css" href="style.css">
    <script src="script.js" defer></script>
    <link rel="icon" type="image/x-icon" href="favicon.png">
</head>
<body>
    <div class="container">
        <h1>GIRL <i>Git Information Retrieval and Lookup</i></h1>
        <div class="navbar">
            <a href="#head" onclick="showSection('head')">HEAD</a> |
            <a href="#refs" onclick="showSection('refs')">Refs</a> |
            <a href="#config" onclick="showSection('config')">Config</a>
        </div>
        <h2>Repository Name</h2>
        <p>{repo_name}</p>
        <h2>Project Tree</h2>
        {project_tree}
        <h2>README.md / LICENSE</h2>
        <div>
            <a href="javascript:void(0);" id="show-readme" onclick="showReadme(event)">README.md</a> |
            <a href="javascript:void(0);" id="show-license" onclick="showLicense(event)">LICENSE</a>
        </div>
        <div id="readme-container">
            <h2>README.md</h2>
            <pre id="readme">{readme}</pre>
        </div>
        <div id="license-container" style="display: none;">
            <h2>LICENSE</h2>
            <pre id="license">{license}</pre>
        </div>
        <div id="head-container" style="display: none;">
            <h2>HEAD</h2>
            <pre>{head}</pre>
        </div>
        <div id="refs-container" style="display: none;">
            <h2>Refs</h2>
            {refs}
        </div>
        <div id="config-container" style="display: none;">
            <h2>Config</h2>
            <pre>{config}</pre>
        </div>
    </div>
</body>
</html>
"""
        return html_content.format(
            repo_name=info_dict.get('Repository Name', ''),
            project_tree=info_dict.get('Project Tree', ''),
            config=info_dict.get('Config', ''),
            head=info_dict.get('HEAD', ''),
            refs=info_dict.get('Refs', ''),
            readme=info_dict.get('README.md', ''),
            license=info_dict.get('LICENSE', '')
        )
    except KeyError as e:
        print(f"KeyError: {e}")
        print("Available keys:", info_dict.keys())
        raise


def main(repo_path):
    """Main function to read .git folder and generate HTML page."""
    git_path = os.path.join(repo_path, '.git')
    info = {}

    repo_name = os.path.basename(os.path.abspath(repo_path))
    info['Repository Name'] = repo_name

    if os.path.isdir(git_path):
        # Read .git/config
        config_path = os.path.join(git_path, 'config')
        if os.path.isfile(config_path):
            info['Config'] = read_file(config_path)
        
        # Read .git/HEAD
        head_path = os.path.join(git_path, 'HEAD')
        if os.path.isfile(head_path):
            info['HEAD'] = read_file(head_path)
        
        # Read .git/refs
        refs_path = os.path.join(git_path, 'refs')
        if os.path.isdir(refs_path):
            refs_content = []
            for root, dirs, files in os.walk(refs_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    refs_content.append(f"{file_path}:<br><pre>{encode_base64(file_path)}</pre>")
            info['Refs'] = "<br>".join(refs_content)

        # Read README.md
        readme_path = os.path.join(repo_path, 'README.md')
        if os.path.isfile(readme_path):
            info['README.md'] = render_markdown(read_file(readme_path))
        
        # Read LICENSE
        license_path = os.path.join(repo_path, 'LICENSE')
        if os.path.isfile(license_path):
            info['LICENSE'] = read_file(license_path)

        # Generate Project Tree
        info['Project Tree'] = generate_tree_html(repo_path, repo_path)

        # Generate HTML content
        html_content = generate_html(info)
        
        # Write HTML to file with UTF-8 encoding
        with open('git_info.html', 'w', encoding='utf-8') as html_file:
            html_file.write(html_content)
        
        print("HTML file 'git_info.html' has been generated.")
    else:
        print("The specified path is not a git repository.")


if __name__ == "__main__":
    # Specify the path to your git repository
    repo_path = '.'
    main(repo_path)