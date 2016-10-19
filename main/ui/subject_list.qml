import QtQuick 2.0
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.3

Item {

    ToolBar {
    id: toolbar
        RowLayout {
            anchors.fill: parent

            ToolButton {
                text: "Add Subject"
            }
            ToolButton {
                text: "Add Teachers"
            }
            ToolButton {
                text: "Add Students"
            }
        }
    }

    ListView {
        id: subject_list_view
        anchors.top: toolbar.bottom
    }
}
