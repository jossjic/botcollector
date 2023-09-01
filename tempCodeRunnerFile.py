    @staticmethod            
    def count_type(model, condition):
        count = 0
        for Basura in model.schedule.agents:
            if Basura.condition == condition:
                count += 1
                print(count)
        return count       
