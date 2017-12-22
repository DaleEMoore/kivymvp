#!/usr/bin/env python3

# Let user pick original kivymvp or kivymvpSQL.
# Switch back and forth between kivymvp and kivymvpSQL?
# https://stackoverflow.com/questions/29332868/is-it-possible-to-read-from-more-than-one-kv-file-in-kivy-app
# https://stackoverflow.com/questions/31458331/running-multiple-kivy-apps-at-same-time-that-communicate-with-each-other
# https://stackoverflow.com/questions/24335870/prevent-the-exit-of-a-kivy-app-on-android-with-the-escape-arrow

import sys
import kivymvp
import kivymvpSQL

if __name__ == '__main__':

    # ask user what they want to run
    #   1: original kivymvp
    #   2: kivymvpSQL

    print("kivymvp.main()")
    try:
        kivymvp.main()
    except:
        print ("Unexpected error:", sys.exc_info()[0])
        #print("An exception occurred: ")

    # gets " AttributeError: __exit__". Fixed by adding __exit__ to AppController class.
    #with kivymvp.main() as first:
    #    print("kivymvp.main in with")
    #    pass

    #print("exit() next.")
    #exit()

    # doesn't run kivymvp.main() then kivymvpSQL.main(). 2nd run doesn't work; no listeners
    #f = kivymvp.main()

    # doesn't run kivymvp.main() then kivymvpSQL.main(). 2nd run doesn't work; no listeners
    #kivymvp.main()

    # TODO; 2nd run doesn't work. There are some good hints here:
    # https://stackoverflow.com/questions/38289017/python-spyder-initializing-hello-world-kivi-app-once
    # Hmmmmm. Run, Edit Configurations, main, Python Interpreter is 3; as it should be.
    """
    __main__.ColorLayout._update_rect()
    [ERROR  ] [Base        ] No event listeners have been created
    [ERROR  ] [Base        ] Application will leave
    AppController.__init__.KivyMVPApp.on_stop()
    """
    print("kivymvpSQL.main()")
    try:
        kivymvpSQL.main()
    except:
        print ("Unexpected error:", sys.exc_info()[0])
    # I wonder if there's something that needs clearing or resetting?
    #print("kivymvpSQL.main()")
    #with kivymvpSQL.main() as second:
    #    print("kivymvpSQL.main in with")
    #   pass
    #f = kivymvpSQL.main()
    #kivymvpSQL.main()
    print("Done")

