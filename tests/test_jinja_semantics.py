from ansibleguard.jinja_semantics import EvaluationState, evaluate_pure_template


def test_bounded_evaluator_handles_literals_and_visible_static_variables():
    assert evaluate_pure_template("{{ true }}").value is True
    assert evaluate_pure_template("{{ 5 }}").value == 5
    assert evaluate_pure_template("{{ [] }}").value == []
    result = evaluate_pure_template("{{ retries }}", {"retries": 3})
    assert result.state == EvaluationState.STATIC
    assert result.value == 3


def test_bounded_evaluator_preserves_known_values_through_default_filters():
    result = evaluate_pure_template(
        "{{ check_mode | default(false) | default(true) }}",
        {"check_mode": False},
    )
    assert result.state == EvaluationState.STATIC
    assert result.value is False
    literal = evaluate_pure_template("{{ true | default(false) }}")
    assert literal.state == EvaluationState.STATIC
    assert literal.value is True


def test_bounded_evaluator_abstains_from_filters_calls_and_runtime_variables():
    for expression in (
        "{{ supplied_by_inventory }}",
        "{{ value | default(true) }}",
        "{{ value | default(true, true) }}",
        "{{ value | arista.avd.default(true) }}",
        "{{ lookup('env', 'VALUE') }}",
        "{{ left and right }}",
    ):
        assert evaluate_pure_template(expression).state == (
            EvaluationState.RUNTIME_UNKNOWN
        )


def test_bounded_evaluator_does_not_treat_non_template_text_as_expression():
    result = evaluate_pure_template("true")
    assert result.state == EvaluationState.NOT_TEMPLATE
    assert result.value == "true"
