class CloudWatchEvent:

    def __init__(self,
                 schedule_expression: str,
                 is_active: bool,
                 name: str =None):
        self.name = name
        self.schedule_expression = schedule_expression
        self.is_active = is_active
