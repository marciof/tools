package joi;


import joi.ui.text.InspectorConsole;


/**
 * Java object inspector.
 *
 * @todo Review code (comments, strings, etc).
 * @todo Make this class as easy to use as
 *       <pre>new Inspector(new Console())</pre> or
 *       <pre>new Inspector(new Windosw())</pre>.
 * @todo Improve the textual and/or add a graphical interface?
 *       <ul>
 *         <li>http://thestaticvoid.net/drivel/90/inspector</li>
 *         <li>http://www.ibm.com/developerworks/lotus/library/expeditor-swt/</li>
 *       </ul>
 */
public class Inspector {
    public static void main(String[] args) {
        Inspector self = new Inspector();
        self.inspect(self);
    }
    

    /**
     * Inspects an object.
     * 
     * @param object object to inspect
     */
    public void inspect(Object object) {
        new InspectorConsole().start(object);
    }
}
