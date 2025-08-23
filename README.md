Syllabus Factory
================

This repository is a factory for producing course syllabi. It uses a TOML
configuration layer to populate information in a set of markdown files, which
are then rendered into a single Word document.

**File tree**

```
├── assets          [Untracked] Assets for Word doc rendering
├── config          Course syllabi TOML
├── docs            Markdown templates for each piece of a syllabus
├── filters         Lua filters for Pandoc
├── src             Python scripts for asset downloads and compiling markdown
├── syllabi         [Untracked] Makefile output
│   ├── docx        Rendered syllabi
│   ├── html        Webpage versions of syllabi
│   └── md          Compiled markdown
├── Makefile        Makefile for creating a syllabus
└── README.md       Repository README
```

**Dependencies**

+ [`make`][make] >= 3.8
+ [`pandoc`][pandoc] >= 3.0
+ [`python`][python] >= 3.10

[make]: https://www.gnu.org/software/make
[pandoc]: https://pandoc.org
[python]: https://www.python.org


Creating a Syllabus
-------------------

To create a syllabus, do the following:

1. Make a new config file and save it to `configs` using the format
   `<YYYY>_<COURSE-CODE>_<COURSE-NAME>.toml`

2. (Optional) Set an environment variable that corresponds to the config file
   ```sh
   export CONFIG=path/to/<YYYY>_<COURSE-CODE>_<COURSE-NAME>.toml
   ```

3. Compile the markdown
   ```sh
   make md
   ```

4. Fill out the schedule in `syllabi/md/<YYYY>_<COURSE-CODE>_<COURSE-NAME>.md`

5. Download a .docx reference file from the Minimum Syllabus Requirements page.
   It will automatically save to `assets/template.docx`
   ```sh
   make get-ref
   ```
   You do not need to run this step again once you have this file

6. Render the markdown to a Word doc
   ```sh
   make docx
   ```

7. (Optional) Render the markdown to an HTML doc
   ```sh
   make html
   ```

Need help? Run the following to see available targets

```sh
make help
```

