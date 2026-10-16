def check_element_threshold(self, element, tier1status, tier2status):
    """apply elemental status effect when reach elemental threshold"""
    status_list = self.status_list
    if element > 50:  # apply tier 1 status
        self.apply_effect(status_list[tier1status], status_list[status_list[tier1status]],
                          self.status_effect, self.status_duration)
        if element > 100:  # apply tier 2 status
            self.apply_effect(status_list[tier2status], status_list[status_list[tier2status]],
                              self.status_effect, self.status_duration)
            element = 0  # reset elemental count
    elif element < 0:
        element = 0
    return element
