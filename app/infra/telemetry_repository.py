from datetime import datetime


class TelemetryRepository:

    def save_event(self, event_name: str, payload: dict):

        telemetry_log = {
            "event": event_name,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat()
        }

        print("TELEMETRY EVENT:", telemetry_log)

        return telemetry_log