me_elapsed = time_step

            for sound in self.sound_objects:
                sound.update(self.time_elapsed)

            for bat in self.bats:
                bat.update(self.time_elapsed, self.sound_objects, temporal_masking_file)

            for jammer in self.jammers:
                jammer.update(self.time_elapsed, self.sound_objects)

            self.handle_reflections(self.time_elapsed)

            self.sound_objects = [
                s
                for s in self.sound_objects
                if s.active and s.current_spl > self.parameters_df["HEARING_THRESHOLD"]
            ]

            self.history.append(self.convert_necessary_information_into_dict())
            current_loop_time = datetime.now()
            list_time_taken_for_each_loop.append(
                current_loop_time - save_time_of_last_iter
            )

            save_time_of_last_iter = current_loop_time

            if self.store_history:
                # self.handle_data_storage_for_plotting(self.time_elapsed, False)
                self.handle_data_storage_for_plotting_pickle(self.time_elapsed, False)