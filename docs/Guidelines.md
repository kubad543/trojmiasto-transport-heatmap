## Documentation Guidelines
These guidelines should be followed for any documentation and research
that should be included in the project.
Any changes done to this should be directly done on the main branch.

### Location
Apart from the `README.md` file all text documents should be located in the
`docs` folder. Each document should have an informative name.
Long names are preferable to make navigating easier.
Please follow **snake_case** in file names.
If you consider files to be related group them into folders.

### Contents
Files should be split into two categories representing their contents.
Filenames ending with `_D` should contain documentation for the created code.
Filenames ending with `-P` should contain project reports.

#### Documentation Contents
These documentation files should contain how a every module works.
Any person who would need to interact with another module (or file)
should be able to know at least the contents of the module.
If all relevant functions are well documented inside the code a short
abstract is sufficient in the documentation.

Well documented means:
- A functions purpose is clear
- All input parameters are described
- All output values are described
- The function is less than 10 lines or has additional comments describing it.


#### Report Contents
The report should be very short.
It should contain only information regarding what the task required.
These files should represent work done other than what is in the codebase.
If the relevant code has not yet been merged with main the branch should be mentioned here.

This includes the following:
- Gathering information (with sources)
- Any subtasks that were relevant
- Who worked on the task
- Any tests that were done to achieve the result.

Tests in this case means any scrapped ideas. 
**Code snippets** are preferred here.
