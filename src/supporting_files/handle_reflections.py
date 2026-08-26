from agents.class_sounds import DirectSound
from supporting_files.utilities import creation_time_calculation


def handle_reflections(self, current_time):
    """Generates reflections of the sound objects.
    Soud objects can reflect off of obstacles and bats
    to generate EchoSound s.

    Args:
        current_time (float): Time, in seconds, for which the simualtion has been running.
    """
    new_echoes = []

    for sound in self.sound_objects:
        if not sound.active or not isinstance(sound, DirectSound):
            continue

        reflection_point = None
        normal = None
        obstacle_id = None

        reflection_point_arr, normal_arr, obstacle_id_arr = [], [], []

        # check walls
        for wall_objects in self.wall_objects:
            # check only for jammer call emissions.

            jammer_wall_check = sound.wall_id != wall_objects.wall_id
            # print(sound, sound.wall_id, wall_objects.wall_id)
            if (
                sound.contains_point(wall_objects.position)
                and f"wall_obstacle_{wall_objects.id}" not in sound.reflected_obstacles
                and jammer_wall_check
            ):
                normal = wall_objects.get_reflection_normal(sound.origin)
                reflection_point = wall_objects.position + normal * wall_objects.radius
                obstacle_id = f"wall_obstacle_{wall_objects.id}"

                normal_arr.append(normal)
                reflection_point_arr.append(reflection_point)
                obstacle_id_arr.append(obstacle_id)
        # check obstacles
        for obstacle in self.obstacles:
            if (
                sound.contains_point(obstacle.position)
                and f"obstacle_{obstacle.id}" not in sound.reflected_obstacles
            ):
                normal = obstacle.get_reflection_normal(sound.origin)
                reflection_point = obstacle.position + normal * obstacle.radius
                obstacle_id = f"obstacle_{obstacle.id}"

                normal_arr.append(normal)
                reflection_point_arr.append(reflection_point)
                obstacle_id_arr.append(obstacle_id)

        # check other bats
        for bat in self.bats:
            if (
                sound.contains_point(bat.position)
                and sound.emitter_id != bat.id
                and f"bat_{bat.id}" not in sound.reflected_obstacles
                and bat.is_bat_reflective_to_sound
            ):
                normal = (sound.origin - bat.position).normalize()
                reflection_point = bat.position + normal * bat.radius
                obstacle_id = f"bat_{bat.id}"

                normal_arr.append(normal)
                reflection_point_arr.append(reflection_point)
                obstacle_id_arr.append(obstacle_id)

        for i, reflection_point in enumerate(reflection_point_arr):
            normal = normal_arr[i]
            obstacle_id = obstacle_id_arr[i]
            if obstacle_id not in sound.reflected_obstacles:
                time_of_creation = creation_time_calculation(sound, reflection_point)

                echo = sound.create_echo(
                    reflection_point, time_of_creation, normal, obstacle_id
                )

                if echo:
                    # mark this obstacle as reflected for the original sound
                    echo.update(current_time)
                    sound.reflected_obstacles.add(obstacle_id)
                    # copy reflected obstacles to the echo
                    echo.reflected_obstacles.update(sound.reflected_obstacles)
                    new_echoes.append(echo)

    self.sound_objects.extend(new_echoes)
