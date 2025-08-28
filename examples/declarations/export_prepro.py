from lukefi.metsi.domain.exp_ops import *

default = {}  # Empty dict declares a default output content

mela_decl = {
    'additional_variables': ['VAR0', 'VAR1', 'VAR2', 'VAR_RANDOM'],
    'operations': [prepare_rst_output, classify_values_to],
    'operation_params': {
        classify_values_to: [
            {'format': 'rst'}
        ]
    }
}


mela = {
    'rst': mela_decl,
    'rsts': mela_decl,
}

mela_and_default_csv = {
    'rst': mela_decl,
    'rsts': mela_decl,
    'csv': default,
}

default_csv = {
    'csv': default
}

csv_and_json = {
    'csv': default,
    'json': default
}

__all__ = ['mela', 'default_csv', 'mela_and_default_csv', 'csv_and_json']
