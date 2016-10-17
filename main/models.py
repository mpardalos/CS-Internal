class Subject:
    def __init__(self, name: str, periods_per_week: int) -> None:
        self.name = name
        self.periods_per_week = periods_per_week
        self.period_names = ['{}-p{}'.format(name, i) 
                for i in range(1, periods_per_week+1)]
        
    def __eq__(self, other):
        return isinstance(other, type(self)) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return "Subject: {}".format(self.name)


