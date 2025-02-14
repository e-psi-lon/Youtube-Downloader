from typing import Callable, Dict, List
from dataclasses import dataclass

@dataclass
class Event:
    name: str
    data: dict

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_name: str, callback: Callable):
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)
    
    def publish(self, event: Event):
        for callback in self._subscribers.get(event.name, []):
            callback(event.data)