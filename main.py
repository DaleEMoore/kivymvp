#!/usr/bin/env python3

# Let user pick original kivymvp or kivymvpSQL.
# Switch back and forth between kivymvp and kivymvpSQL?
# https://stackoverflow.com/questions/29332868/is-it-possible-to-read-from-more-than-one-kv-file-in-kivy-app
# https://stackoverflow.com/questions/31458331/running-multiple-kivy-apps-at-same-time-that-communicate-with-each-other
# https://stackoverflow.com/questions/24335870/prevent-the-exit-of-a-kivy-app-on-android-with-the-escape-arrow

import kivymvp
import kivymvpSQL

if __name__ == '__main__':

    # ask user what they want to run
    #   1: original kivymvp
    #   2: kivymvpSQL

    print("kivymvp.main()")

    # gets " AttributeError: __exit__". Fixed by adding __exit__ to AppController class.
    with kivymvp.main() as first:
        print("kivymvp.main in with")
        pass

    # doesn't run kivymvp.main() then kivymvpSQL.main(). 2nd run doesn't work; no listeners
    #f = kivymvp.main()

    # doesn't run kivymvp.main() then kivymvpSQL.main(). 2nd run doesn't work; no listeners
    #kivymvp.main()

    # TODO; 2nd run doesn't work
    """
    __main__.ColorLayout._update_rect()
    [ERROR  ] [Base        ] No event listeners have been created
    [ERROR  ] [Base        ] Application will leave
    AppController.__init__.KivyMVPApp.on_stop()
    """
    # I wonder if there's something that needs clearing or resetting?
    print("kivymvpSQL.main()")
    with kivymvpSQL.main() as second:
        print("kivymvpSQL.main in with")
        pass
    #f = kivymvpSQL.main()
    #kivymvpSQL.main()
    print("Done")

