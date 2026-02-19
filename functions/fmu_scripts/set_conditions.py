
def set_conditions(conditions, fmu, vrs, initial_conditions=False, model_description=None, verbose=False):
    if conditions is not None:
        if initial_conditions == False:
            if model_description is not None:
                types = {var.name: var.type for var in model_description.modelVariables}  # map variable names to types
                
                for key, value in conditions.items():
                    vtype = types.get(key, None)

                    try:
                        if vtype == "Real":
                            fmu.setReal([vrs[key]], [float(value)])
                            if verbose: print(f"Condition: {key} set to {value} (Real)")
                        elif vtype == "Integer":
                            fmu.setInteger([vrs[key]], [int(value)])
                            if verbose: print(f"Condition: {key} set to {value} (Integer)")
                        elif vtype == "Boolean":
                            fmu.setBoolean([vrs[key]], [bool(value)])
                            if verbose: print(f"Condition: {key} set to {value} (Boolean)")
                        elif vtype == "String":
                            fmu.setString([vrs[key]], [str(value)])
                            if verbose: print(f"Condition: {key} set to {value} (String)")
                        else:
                            if verbose: print(f"Unknown type for {key}")

                    except Exception as e:
                        print(f"Failed to set {key} to {value}: {e}")
                    
            else:
                for key, value in conditions.items():
                    if isinstance(value, bool):
                        fmu.setBoolean([vrs[key]], [value])
                        if verbose: print(f"Condition: {key} set to {value} (Boolean)")
                    elif isinstance(value, (int, float)):
                        fmu.setReal([vrs[key]], [value])
                        if verbose: print(f"Condition: {key} set to {value} (Real)")
                    else:
                        if verbose: print(f"Couldn't process condition {key}\n")
        else:
            # set initial conditions
            for key, value in conditions.items():
                try: fmu.setReal([vrs[key]], [value])
                except: pass
