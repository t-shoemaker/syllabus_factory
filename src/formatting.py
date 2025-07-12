from string import Template


class Formatter:
    templates = {
        "objectives": Template("+ $description"),
        "books": Template("+ $author. $title ($isbn)"),
        "assignments": Template("| $due | $points | $name |"),
        "weeks": Template("**[Week $num]{.smallcaps}**"),
        "days": Template("$weekday ($month/$day)"),
    }

    def format(self, content, template=""):
        """Format content with a template.

        Parameters
        ----------
        content : list[dict]
            Content to format
        template : str
            The template to use

        Returns
        -------
        str
            Formatted content

        Raises
        ------
        ValueError
            If a template is unavailable
        """
        if template not in self.templates:
            raise ValueError(f"Template '{template}' not implemented")

        template = self.templates[template]
        output = [template.safe_substitute(**item) for item in content]
        return "\n".join(output)
