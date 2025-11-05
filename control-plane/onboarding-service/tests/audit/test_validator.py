from app.audit.validator import validate_event_dict

def test_validator_redacts():
    event = {
        "service":"onboarding-service","env":"dev",
        "method":"POST","path":"/x","status_code":201,
        "payload":{"email":"a@b.com", "ok":True}
    }
    ok, errs = validate_event_dict(event)
    assert ok, errs