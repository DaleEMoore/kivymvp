#!/usr/bin/env python3

# Let user pick original kivymvp or kivymvpSQL.

import kivymvp
import kivymvpSQL

if __name__ == '__main__':

    # ask user what they want to run
    #   1: original kivymvp
    #   2: kivymvpSQL

    print("kivymvp.main()")
    kivymvp.main()
    # TODO; 2nd run doesn't work
    """
    __main__.ColorLayout._update_rect()
    [ERROR  ] [Base        ] No event listeners have been created
    [ERROR  ] [Base        ] Application will leave
    AppController.__init__.KivyMVPApp.on_stop()
    """
    # I wonder if there's something that needs clearing or resetting?
    print("kivymvpSQL.main()")
    kivymvpSQL.main()
    print("Done")

