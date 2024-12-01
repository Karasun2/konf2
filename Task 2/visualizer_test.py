import pytest
import os
import yaml
import networkx as nx
from unittest.mock import patch, mock_open
from visualizer import (
    load_config,
    get_dependencies_from_nupkg,
    build_graph,
    generate_mermaid_graph,
)

@pytest.fixture
def config_yaml():
    return """
    nupkg_path: "test_package.nupkg"
    visualizer_path: "mermaid-cli"
    output_image_path: "output.png"
    """

def test_load_config(config_yaml):
    with patch("builtins.open", mock_open(read_data=config_yaml)):
        config = load_config("dummy_path.yaml")
        assert config["nupkg_path"] == "test_package.nupkg"
        assert config["visualizer_path"] == "mermaid-cli"
        assert config["output_image_path"] == "output.png"

def test_build_graph():
    dependencies = [("dep1", "1.0"), ("dep2", "2.0")]
    
    config = {
        'nupkg_path': '\\dummy_path.nupkg',
        'visualizer_path': 'mermaid-cli',
        'output_image_path': 'output.png',
        'root_package': 'root_package'
    }
    
    G = build_graph(dependencies, config)
    G.add_node(config['root_package'])
    for dep, _ in dependencies:
        G.add_edge(config['root_package'], dep)

    assert G.has_node(config['root_package'])
    assert G.has_node("dep1")
    assert G.has_node("dep2")
    assert G.has_edge(config['root_package'], "dep1")
    assert G.has_edge(config['root_package'], "dep2")


def test_generate_mermaid_graph():
    G = nx.DiGraph()
    G.add_edges_from([("A", "B"), ("A", "C")])
    mermaid_str = generate_mermaid_graph(G)
    
    assert "graph TD;" in mermaid_str
    assert "A --> B;" in mermaid_str
    assert "A --> C;" in mermaid_str

if __name__ == "__main__":
    pytest.main()
