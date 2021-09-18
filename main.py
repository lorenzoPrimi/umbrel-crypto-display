import glob
import logging
import os
import time

try:
    from libs import *
except ImportError as e:
    from .libs import *

next_run = 0


def run_script(
        module_name: str,
        className: str,
        fb: iFB,
        save_image_file: bool,
        output_folder: str,
        refresh_interval: int
):
    global next_run
    script_module = __import__(f"scripts.{module_name}", fromlist=[f"scripts.{module_name}"])
    script_class = getattr(script_module, className)

    if issubclass(script_class, iScriptImageGenerator):
        script_object: iScriptImageGenerator = script_class()
        i = 0
        for im in script_object.generate_all_images(screen_size):
            i += 1
            if next_run > time.time():
                time.sleep(next_run - time.time())
            next_run = time.time() + refresh_interval
            fb.show(im, refresh_interval * 2)
            if save_image_file:
                output_file = os.path.join(output_folder, f"{module_name}-{i}.png")
                im.save(output_file)
            # time.sleep(refresh_interval)

    if issubclass(script_class, iPygameScript):
        script_object: iPygameScript = script_class()
        try:
            script_object.start()
            if refresh_interval > 0:
                time.sleep(refresh_interval)
                script_object.stop()
            script_object.join()
        finally:
            script_object.quit()


if __name__ == '__main__':
    config = Config()

    scripts_dir = os.path.abspath(os.path.join(os.path.basename(__file__), '..', 'scripts'))

    if config.use_fbi:
        fb = Fbi(
            dev_no=config.frame_buffer,
            vt=config.virtual_terminal,
            folder=config.output_folder,
            timeout=config.refresh_interval
        )
    else:
        fb = FrameBuffer(dev_no=config.frame_buffer, vt=config.virtual_terminal)
        fb.validate()

    with fb:
        if config.force_screen_size:
            screen_size = config.force_screen_size
        else:
            screen_size = fb.size

        logging.info(f"script dir: '{scripts_dir}'")
        while True:
            scripts = config.scripts
            if scripts:
                for (module_name, className) in scripts:
                    try:
                        run_script(
                            module_name=module_name,
                            className=className,
                            fb=fb,
                            save_image_file=config.save_image_file,
                            output_folder=config.output_folder,
                            refresh_interval=config.refresh_interval
                        )
                    except Exception as e:
                        logging.exception(e)
            else:
                for filepath in glob.glob(os.path.join(scripts_dir, "*.py")):
                    try:
                        filename = os.path.basename(filepath)
                        run_script(
                            module_name=filename[:-3],
                            className="Script",
                            fb=fb,
                            save_image_file=config.save_image_file,
                            output_folder=config.output_folder,
                            refresh_interval=config.refresh_interval
                        )
                    except Exception as e:
                        logging.exception(e)
