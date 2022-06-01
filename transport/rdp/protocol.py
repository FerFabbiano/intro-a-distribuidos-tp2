import time

TIMER_TICK_SECONDS = 0.010

class RdpProtocolHelper:
    """
    Singleton helper service for reliable UDP (rUDP) connections.

    This class keeps global state across rUDP connections and does
    some bookeeping such as running timers.
    """

    _instance = None

    @staticmethod
    def instance():
        if RdpProtocolHelper._instance is None:
            RdpProtocolHelper._instance = RdpProtocolHelper()
        return RdpProtocolHelper._instance
    
    @staticmethod
    def shutdown():
        self.instance().stop()

    def __init__(self):
        """
        This constructor must not be invoked directly!!
        Use RdpProtocolHelper.instance() instead
        """
        self.connections = {}
        self.keep_alive = True
    
    def stop(self):
        self.keep_alive = False

    def _run_timers(self):
        while self.keep_alive:
            time.sleep(TIMER_TICK_SECONDS)

            connections_to_pop = []
            for client_address, connection in self.connections.items():
                if not connection.is_alive():
                    connections_to_pop.append(client_address)
                else:
                    connection.on_tick(time.time())
            
            for client_address in connections_to_pop:
                self.connections.popitem(client_address)