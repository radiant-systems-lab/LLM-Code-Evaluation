# Logging and Configuration Management
import logging
import logging.config
import configparser
import argparse
import sys
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import yaml
import json
from pathlib import Path

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CustomFormatter(logging.Formatter):
    """Custom log formatter with colors"""
    
    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    def __init__(self):
        super().__init__()
        self.FORMATS = {
            logging.DEBUG: self.grey + "[%(asctime)s] %(name)s - %(levelname)s - %(message)s" + self.reset,
            logging.INFO: self.blue + "[%(asctime)s] %(name)s - %(levelname)s - %(message)s" + self.reset,
            logging.WARNING: self.yellow + "[%(asctime)s] %(name)s - %(levelname)s - %(message)s" + self.reset,
            logging.ERROR: self.red + "[%(asctime)s] %(name)s - %(levelname)s - %(message)s" + self.reset,
            logging.CRITICAL: self.bold_red + "[%(asctime)s] %(name)s - %(levelname)s - %(message)s" + self.reset
        }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def setup_advanced_logging():
    """Setup advanced logging configuration"""
    # Create logs directory
    log_dir = Path('/tmp/logs')
    log_dir.mkdir(exist_ok=True)
    
    # Configure multiple handlers
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'detailed',
                'filename': str(log_dir / 'application.log'),
                'maxBytes': 1024*1024*5,  # 5MB
                'backupCount': 3
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'formatter': 'detailed',
                'filename': str(log_dir / 'errors.log')
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console', 'file', 'error_file'],
                'level': 'DEBUG',
                'propagate': False
            }
        }
    })
    
    return logging.getLogger(__name__)

def configuration_management():
    """Demonstrate configuration management"""
    # Create sample config file
    config_path = '/tmp/app_config.ini'
    
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'debug': 'false',
        'log_level': 'INFO',
        'timeout': '30'
    }
    config['database'] = {
        'host': 'localhost',
        'port': '5432',
        'name': 'myapp',
        'username': 'admin'
    }
    config['api'] = {
        'base_url': 'https://api.example.com',
        'version': 'v1',
        'rate_limit': '1000'
    }
    
    # Write config file
    with open(config_path, 'w') as configfile:
        config.write(configfile)
    
    # Read config file
    loaded_config = configparser.ConfigParser()
    loaded_config.read(config_path)
    
    # Access config values
    db_host = loaded_config['database']['host']
    api_rate_limit = loaded_config.getint('api', 'rate_limit')
    debug_mode = loaded_config.getboolean('DEFAULT', 'debug')
    
    return {
        'config_sections': len(loaded_config.sections()),
        'db_host': db_host,
        'api_rate_limit': api_rate_limit,
        'debug_mode': debug_mode
    }

def yaml_configuration():
    """YAML configuration management"""
    config_data = {
        'application': {
            'name': 'MyApp',
            'version': '1.0.0',
            'environment': 'production'
        },
        'logging': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        },
        'database': {
            'driver': 'postgresql',
            'host': 'localhost',
            'port': 5432,
            'credentials': {
                'username': 'admin',
                'password': 'secret'
            }
        },
        'features': {
            'feature_flags': {
                'new_ui': True,
                'beta_features': False,
                'analytics': True
            }
        }
    }
    
    # Write YAML config
    yaml_path = '/tmp/config.yaml'
    with open(yaml_path, 'w') as f:
        yaml.dump(config_data, f, default_flow_style=False)
    
    # Read YAML config
    with open(yaml_path, 'r') as f:
        loaded_config = yaml.safe_load(f)
    
    return {
        'app_name': loaded_config['application']['name'],
        'app_version': loaded_config['application']['version'],
        'enabled_features': sum(loaded_config['features']['feature_flags'].values()),
        'db_port': loaded_config['database']['port']
    }

def command_line_parsing():
    """Command line argument parsing"""
    parser = argparse.ArgumentParser(description='Sample Application')
    
    # Add arguments
    parser.add_argument('--config', '-c', type=str, default='config.ini',
                       help='Configuration file path')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--port', '-p', type=int, default=8080,
                       help='Server port number')
    parser.add_argument('--environment', '-e', choices=['dev', 'test', 'prod'],
                       default='dev', help='Environment')
    parser.add_argument('--workers', '-w', type=int, default=4,
                       help='Number of worker processes')
    parser.add_argument('--features', nargs='+', default=[],
                       help='List of features to enable')
    
    # Parse arguments (using sample arguments)
    sample_args = ['--config', '/tmp/config.ini', '--verbose', '--port', '9000',
                  '--environment', 'prod', '--workers', '8', 
                  '--features', 'feature1', 'feature2']
    
    # Temporarily replace sys.argv for demonstration
    original_argv = sys.argv
    sys.argv = ['script.py'] + sample_args
    
    try:
        args = parser.parse_args()
        return {
            'config_file': args.config,
            'verbose': args.verbose,
            'port': args.port,
            'environment': args.environment,
            'workers': args.workers,
            'features': args.features
        }
    finally:
        sys.argv = original_argv

def environment_configuration():
    """Environment-based configuration"""
    # Set some environment variables for demonstration
    os.environ['APP_DEBUG'] = 'true'
    os.environ['APP_SECRET_KEY'] = 'my-secret-key'
    os.environ['DATABASE_URL'] = 'postgresql://localhost:5432/myapp'
    os.environ['REDIS_URL'] = 'redis://localhost:6379'
    
    # Read environment variables with defaults
    config = {
        'debug': os.getenv('APP_DEBUG', 'false').lower() == 'true',
        'secret_key': os.getenv('APP_SECRET_KEY'),
        'database_url': os.getenv('DATABASE_URL'),
        'redis_url': os.getenv('REDIS_URL'),
        'port': int(os.getenv('PORT', '8000')),
        'workers': int(os.getenv('WORKERS', '4')),
        'log_level': os.getenv('LOG_LEVEL', 'INFO').upper()
    }
    
    return config

def structured_logging_example():
    """Structured logging example"""
    # Setup logger with JSON formatter
    import json
    
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                'timestamp': self.formatTime(record),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            
            # Add extra fields if present
            if hasattr(record, 'user_id'):
                log_record['user_id'] = record.user_id
            if hasattr(record, 'request_id'):
                log_record['request_id'] = record.request_id
                
            return json.dumps(log_record)
    
    # Create logger with JSON formatter
    json_logger = logging.getLogger('json_logger')
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    json_logger.addHandler(handler)
    json_logger.setLevel(logging.INFO)
    
    # Log structured messages
    json_logger.info("User login", extra={'user_id': 123, 'request_id': 'abc-123'})
    json_logger.warning("High memory usage", extra={'memory_usage': 85.5})
    json_logger.error("Database connection failed", extra={'error_code': 'DB_001'})
    
    return {'structured_logs': 3}

if __name__ == "__main__":
    print("Logging and configuration management...")
    
    # Setup advanced logging
    advanced_logger = setup_advanced_logging()
    advanced_logger.info("Advanced logging configured")
    advanced_logger.debug("This is a debug message")
    advanced_logger.warning("This is a warning message")
    advanced_logger.error("This is an error message")
    
    # Configuration management
    config_result = configuration_management()
    logger.info(f"Configuration loaded: {config_result}")
    
    # YAML configuration
    yaml_result = yaml_configuration()
    logger.info(f"YAML config: {yaml_result}")
    
    # Command line parsing
    cli_result = command_line_parsing()
    logger.info(f"CLI arguments: {cli_result}")
    
    # Environment configuration
    env_config = environment_configuration()
    logger.info(f"Environment config loaded: {len(env_config)} variables")
    
    # Structured logging
    struct_result = structured_logging_example()
    logger.info(f"Structured logging: {struct_result['structured_logs']} messages logged")