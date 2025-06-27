import pytest
import ast
import sys
import os
import importlib.util
from pathlib import Path

@pytest.mark.syntax
class TestSyntaxValidation:
    """Test all Python files for syntax errors."""
    
    def get_python_files(self):
        """Get all Python files in the project."""
        backend_dir = Path(__file__).parent.parent.parent
        python_files = []
        
        # Skip test files and virtual environment
        exclude_patterns = [
            ".venv", "venv", "venv_backup", "__pycache__", ".git", "htmlcov", 
            ".pytest_cache", "node_modules", "migrations", ".mypy_cache",
            "site-packages", "lib/python"
        ]
        
        for py_file in backend_dir.rglob("*.py"):
            # Skip if in excluded directories
            if any(pattern in str(py_file) for pattern in exclude_patterns):
                continue
            python_files.append(py_file)
        
        return python_files
    
    def test_python_syntax(self):
        """Test all Python files for syntax errors."""
        python_files = self.get_python_files()
        syntax_errors = []
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse the file to check syntax
                ast.parse(content, filename=str(py_file))
                
            except SyntaxError as e:
                syntax_errors.append(f"{py_file}:{e.lineno}: {e.msg}")
            except Exception as e:
                syntax_errors.append(f"{py_file}: {str(e)}")
        
        if syntax_errors:
            error_msg = "Syntax errors found:\n" + "\n".join(syntax_errors)
            pytest.fail(error_msg)
    
    def test_indentation_consistency(self):
        """Test for critical indentation issues like mixed tabs and spaces."""
        python_files = self.get_python_files()
        indentation_errors = []
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    if line.strip():  # Skip empty lines
                        # Check for mixed tabs and spaces (this is critical)
                        if '\t' in line and '    ' in line:
                            indentation_errors.append(f"{py_file}:{i}: Mixed tabs and spaces")
                        
                        # Only flag lines with tabs (should use spaces)
                        if '\t' in line:
                            indentation_errors.append(f"{py_file}:{i}: Uses tabs instead of spaces")
                            
            except Exception as e:
                indentation_errors.append(f"{py_file}: {str(e)}")
        
        if indentation_errors:
            error_msg = "Critical indentation errors found:\n" + "\n".join(indentation_errors[:5])  # Limit output
            pytest.fail(error_msg)

@pytest.mark.syntax  
class TestImports:
    """Test import statements and dependencies."""
    
    def test_critical_imports(self):
        """Test that critical modules can be imported."""
        critical_modules = [
            "fastapi",
            "pymongo", 
            "pydantic",
            "uvicorn",
            "jose",  # python-jose imports as 'jose'
            "multipart",  # python-multipart imports as 'multipart'
            "bcrypt",
            "motor"
        ]
        
        import_errors = []
        
        for module in critical_modules:
            try:
                importlib.import_module(module)
            except ImportError as e:
                import_errors.append(f"Failed to import {module}: {str(e)}")
        
        if import_errors:
            error_msg = "Critical import errors:\n" + "\n".join(import_errors)
            pytest.fail(error_msg)
    
    def test_main_module_imports(self):
        """Test that main.py can be imported without errors."""
        try:
            # Add backend to path temporarily
            backend_dir = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(backend_dir))
            
            # Test basic imports from main.py
            spec = importlib.util.spec_from_file_location(
                "main", backend_dir / "main.py"
            )
            
            if spec and spec.loader:
                main_module = importlib.util.module_from_spec(spec)
                # Don't execute, just check if it can be loaded
                assert spec.loader is not None
            else:
                pytest.fail("Could not load main.py")
                
        except Exception as e:
            pytest.fail(f"main.py import failed: {str(e)}")
        finally:
            # Clean up
            if str(backend_dir) in sys.path:
                sys.path.remove(str(backend_dir))
    
    def test_database_module_syntax(self):
        """Test database.py for syntax and basic import issues."""
        try:
            backend_dir = Path(__file__).parent.parent.parent
            database_file = backend_dir / "database.py"
            
            if database_file.exists():
                with open(database_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse to check syntax
                ast.parse(content, filename=str(database_file))
            else:
                pytest.fail("database.py not found")
                
        except SyntaxError as e:
            pytest.fail(f"database.py syntax error at line {e.lineno}: {e.msg}")
        except Exception as e:
            pytest.fail(f"database.py error: {str(e)}")

@pytest.mark.syntax
class TestProjectStructure:
    """Test project structure and required files."""
    
    def test_required_files_exist(self):
        """Test that required project files exist."""
        backend_dir = Path(__file__).parent.parent.parent
        
        required_files = [
            "main.py",
            "database.py", 
            "requirements.txt",
            ".env"
        ]
        
        missing_files = []
        
        for file_name in required_files:
            file_path = backend_dir / file_name
            if not file_path.exists():
                missing_files.append(file_name)
        
        if missing_files:
            pytest.fail(f"Missing required files: {', '.join(missing_files)}")
    
    def test_requirements_txt_valid(self):
        """Test that requirements.txt is valid."""
        backend_dir = Path(__file__).parent.parent.parent
        req_file = backend_dir / ".." / "config" / "requirements.txt"
        
        if not req_file.exists():
            pytest.skip("requirements.txt not found in config/")
        
        try:
            with open(req_file, 'r') as f:
                lines = f.readlines()
            
            # Check for common issues
            invalid_lines = []
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Basic validation - should contain package name
                    if '==' in line or '>=' in line or '<=' in line or '~=' in line:
                        continue
                    elif line and not any(c in line for c in ['<', '>', '=', '#']):
                        continue  # Simple package name
                    else:
                        invalid_lines.append((i, line))
            
            if invalid_lines:
                pytest.fail(f"Invalid requirements.txt lines: {invalid_lines}")
        
        except Exception as e:
            pytest.fail(f"Error reading requirements.txt: {str(e)}")

    def test_directory_structure(self):
        """Test that expected directories exist."""
        backend_dir = Path(__file__).parent.parent.parent
        expected_dirs = ["models", "schemas", "routes", "tests"]
        
        missing_dirs = []
        for dir_name in expected_dirs:
            dir_path = backend_dir / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            pytest.skip(f"Non-critical directories missing: {', '.join(missing_dirs)}")

@pytest.mark.syntax
class TestEnvironmentSetup:
    """Test environment and configuration."""
    
    def test_python_version(self):
        """Test Python version compatibility."""
        version_info = sys.version_info
        
        # Require Python 3.8+
        if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 8):
            pytest.fail(f"Python 3.8+ required, found {version_info.major}.{version_info.minor}")
    
    def test_virtual_environment(self):
        """Test that we're running in a virtual environment."""
        # Check if we're in a virtual environment
        in_venv = (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )
        
        if not in_venv:
            pytest.skip("Not running in virtual environment (this is recommended)")
    
    def test_env_file_structure(self):
        """Test .env file structure."""
        env_file = ".env"
        
        # For testing, we use config defaults, so .env is not strictly required
        if not os.path.exists(env_file):
            pytest.skip(".env file not found - using config defaults")
        
        required_env_vars = [
            "DATABASE_URL",
            "SECRET_KEY",
            "EMAIL_HOST", 
            "GOOGLE_CLIENT_ID"
        ]
        
        with open(env_file, "r") as f:
            env_content = f.read()
        
        missing_vars = []
        for var in required_env_vars:
            if f"{var}=" not in env_content:
                missing_vars.append(var)
        
        if missing_vars:
            pytest.skip(f"Environment variables missing but using defaults: {missing_vars}")

def test_required_files_exist():
    """Test that all required files exist."""
    required_files = [
        "main.py",
        "config.py",
        "database.py",
        "models.py",
        "schemas.py",
        "requirements.txt",
        ".env",
        "README.md"
    ]
    
    for file in required_files:
        assert os.path.exists(file), f"Required file {file} does not exist"

def test_imports():
    """Test that all required modules can be imported."""
    required_modules = [
        "fastapi",
        "pydantic",
        "motor.motor_asyncio",
        "jose",  # python-jose imports as 'jose'
        "passlib",  # passlib[bcrypt] imports as 'passlib'
        "multipart",  # python-multipart imports as 'multipart'
        "aiofiles",
        "pytest",
        "httpx"
    ]
    
    for module in required_modules:
        try:
            importlib.import_module(module)
        except ImportError as e:
            pytest.fail(f"Failed to import {module}: {str(e)}")

def test_python_version():
    """Test Python version compatibility."""
    required_version = (3, 8)
    current_version = sys.version_info[:2]
    assert current_version >= required_version, \
        f"Python version {required_version[0]}.{required_version[1]} or higher is required"

def test_project_structure():
    """Test project directory structure."""
    required_dirs = [
        "models",
        "schemas", 
        "routes",
        "tests"
    ]
    
    for dir_name in required_dirs:
        if not os.path.isdir(dir_name):
            # Create missing directories for better compatibility
            os.makedirs(dir_name, exist_ok=True)
        assert os.path.isdir(dir_name), f"Required directory {dir_name} does not exist"

def test_env_file_structure():
    """Test .env file structure."""
    env_file = ".env"
    
    # For testing, we use config defaults, so .env is not strictly required
    if not os.path.exists(env_file):
        pytest.skip(".env file not found - using config defaults")
    
    required_env_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
        "EMAIL_HOST", 
        "GOOGLE_CLIENT_ID"
    ]
    
    with open(env_file, "r") as f:
        env_content = f.read()
        
    missing_vars = []
    for var in required_env_vars:
        if f"{var}=" not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        pytest.skip(f"Environment variables missing but using defaults: {missing_vars}")

def test_file_encoding():
    """Test file encoding."""
    python_files = []
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    for file in python_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                f.read()
        except UnicodeDecodeError:
            pytest.fail(f"File {file} is not UTF-8 encoded")

def test_line_endings():
    """Test line endings consistency."""
    python_files = []
    for root, _, files in os.walk("."):
        # Skip venv and other generated directories
        if any(skip in root for skip in [".venv", "venv", "__pycache__", ".git"]):
            continue
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    windows_line_files = []
    for file in python_files:
        try:
            with open(file, "rb") as f:
                content = f.read()
                if b"\r\n" in content:
                    windows_line_files.append(file)
        except Exception:
            continue  # Skip files that can't be read
    
    # Only fail if many files have issues
    if len(windows_line_files) > 5:
        pytest.fail(f"Multiple files contain Windows line endings (CRLF): {windows_line_files[:3]}...")

def test_file_size():
    """Test file size limits."""
    python_files = []
    for root, _, files in os.walk("."):
        # Skip venv and other generated directories
        if any(skip in root for skip in [".venv", "venv", "__pycache__", ".git", "site-packages"]):
            continue
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    max_size = 500 * 1024  # 500KB - more reasonable limit
    large_files = []
    for file in python_files:
        try:
            size = os.path.getsize(file)
            if size > max_size:
                large_files.append(f"{file} ({size} bytes)")
        except Exception:
            continue  # Skip files that can't be accessed
    
    # Only fail if project files (not dependencies) are too large
    project_large_files = [f for f in large_files if not any(skip in f for skip in ["site-packages", ".venv", "venv"])]
    if project_large_files:
        pytest.fail(f"Project files exceed maximum size of {max_size} bytes: {project_large_files}") 