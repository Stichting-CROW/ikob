# Input data preprocessing for IKOB

The IKOB programs require a specific set of input data that are extracted
from external data sources. Since these external data sources are updated
every year, or every couple of years, this input preprocessing should be
redone whenever new external data is provided. The process of doing so
is described in [`./input-data-to-ikob-data.docx`](./input-data-to-ikob-data.docx)
and some of the preprocessing are captured in the Python scripts:

* [`./Matrixomnummeren.py`](./Matrixomnummeren.py)
* [`./OVskims-berekenen.py`](./OVskims-berekenen.py)
* [`./Reistijdennaarmatrix_zonder_omnummering.py`](./Reistijdennaarmatrix_zonder_omnummering.py)

