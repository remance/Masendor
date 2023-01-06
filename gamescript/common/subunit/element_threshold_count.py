def element_threshold_count(self, element, tier1status, tier2status):
    """apply elemental status effect when reach elemental threshold"""
    if element > 50:
        self.apply_effect(self.status_list[tier1status], self.status_list, self.status_effect)  # apply tier 1 status
        if element > 100:
            self.apply_effect(self.status_list[tier2status], self.status_list, self.status_effect)  # apply tier 2 status
            element = 0  # reset elemental count
    elif element < 0:
        element = 0
    return element
