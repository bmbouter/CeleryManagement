
class Entry(object):
    def __init__(self, policy, modified, last_run_time=None):
        self.policy = policy
        self.last_run_time = last_run_time
        self.modified = modified
        
    def next_run_time(self):
        self.policy.next_run_time(self.last_run_time)
        
    def is_due(self, current_time):
        return current_time > self.next_run_time()
        
    def set_last_run_time(self, current_time):
        self.last_run_time = current_time
        
    def update(self, **kwargs):
        self.policy = kwargs.pop('policy', self.policy)
        self.last_run_time = kwargs.pop('last_run_time', self.last_run_time)
        self.modified = kwargs.pop('modified', self.modified)


class Registry(object):
    def __init__(self):
        self.data = {}
        
    def __iter__(self):
        return self.data.itervalues()
        
    def register(self, obj):
        assert obj.enabled
        assert obj.id not in self.data
        policy = Policy(source=obj.source, id=obj.id)
        entry = Entry(policy=policy, modified=obj.modified, last_run_time=obj.last_run_time)
        self.data[obj.id] = entry
        
    def reregister(self, obj):
        assert obj.enabled
        entry = self.data[obj.id]
        assert obj.last_run_time is None or obj.last_run_time <= entry.last_run_time
        entry.policy.reinit(source=obj.source)
        entry.update(modified=obj.modified)
        
    def unregister(self, id):
        del self.data[id]
        
    def refresh(self):
        updated = False
        objects = PolicyModel.objects.all()
        for id,entry in self.data.iteritems():
            try:
                obj = objects.get(id)
                if obj.enabled and obj.modified > entry.modified:
                    self.reregister(obj)
                    updated = True
                elif not obj.enabled:
                    self.unregister(id)
                    updated = True
            except ...:
                self.unregister(id)
                updated = True
        
        for obj in objects:
            if obj.enabled and obj.id not in self.data:
                self.register(obj)
                updated = True
        
        return updated
                
    def save(self, id, current_time):
        entry = self.data[id]
        obj = PolicyModel.objects.get(id)
        if obj.modified > entry.modified:
            self.reregister(obj)
        obj.last_run_time = entry.last_run_time
        obj.modified, entry.modified = current_time, current_time
        obj.save()
        


class PolicyMain(object):
    def __init__(self):
        self.registry = Registry()
        self.next_run_time = datetime.datetime.now()
        
    def loop(self):
        self.refresh_registry()
        self.run_ready_policies()
        sleep()
        
    def refresh_registry(self):
        if self.registry.refresh():
            self.update_next_runtime()
            
    def update_next_runtime(self):
        self.next_run_time = min(entry.next_run_time() for entry in self.registry)
        
    def run_ready_policies(self):
        now = datetime.datetime.now()
        if now >= self.next_run_time:
            modified_ids = []
            try:
                for entry in self.registry:
                    if entry.is_due(now):
                        self.run_policy(entry.policy)
                        entry.set_last_run_time(now)
                        modified_ids.append(entry.policy.id)
            finally:
                now = datetime.datetime.now()
                for id in modified_ids
                    self.registry.save(id, now)
                self.update_next_runtime()
            
    def run_policy(self, policy):
        if policy.run_condition():
            policy.run_apply()
        
        
        



