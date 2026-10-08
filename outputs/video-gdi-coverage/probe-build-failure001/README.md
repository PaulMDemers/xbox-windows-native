# Preserved prelaunch compiler failure

RosBE GCC rejected the first probe under unchanged `-Wall -Wextra -Werror`:
misleading indentation on lines70,71,85,108,109, where a conditional/loop and
the next independent statement shared a line. No binary or guest launch.
The corrected probe separates those statements; warning gates remain unchanged.
