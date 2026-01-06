                    obj = {
                        "name": name,
                        "confidence": round(conf, 2),
                        "distance_cm": round(z_cm, 1),
                        "center": [cx, cy],
                        "grasp_center": [cx + GRASP_OFFSET_X, cy + GRASP_OFFSET_Y]
                    }
                    objects.append(obj)