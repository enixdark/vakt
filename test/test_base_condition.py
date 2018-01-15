from vakt.conditions.base import Condition


class ABCondition(Condition):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def satisfied(self, what, request):
        return self.a == self.b


def test_to_json():
    conditions = [
        ABCondition(1, 2),
        ABCondition('x', 'y'),
    ]
    assert '{"type": "ABCondition", "contents": {"a": 1, "b": 2}}' == conditions[0].to_json()
    assert '{"type": "ABCondition", "contents": {"a": "x", "b": "y"}}' == conditions[1].to_json()


def test_from_json():
    conditions = [
        '{"type": "ABCondition", "contents": {"a": 1, "b": 2}}',
        '{"type": "ABCondition", "contents": {"a": "x", "b": "y"}}',
    ]
    assert '' == ABCondition.from_json(conditions[0])
    assert '' == ABCondition.from_json(conditions[1])


def test_name():
    assert 'ABCondition' == ABCondition(1, 2).name()


def test_satisfied():
    assert ABCondition(2, 2).satisfied('a', 'b')
    assert not ABCondition(1, 2).satisfied('a', 'b')
