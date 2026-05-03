from app.schemas import AuditEvent


class AuditTrail:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def add(self, actor: str, action: str, status: str, detail: str, **metadata: object) -> AuditEvent:
        event = AuditEvent(
            actor=actor,
            action=action,
            status=status,
            detail=detail,
            metadata=dict(metadata),
        )
        self.events.append(event)
        return event

