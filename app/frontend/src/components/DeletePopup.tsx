import axios from 'axios';
import Button from '@material-ui/core/Button';
import DeleteIcon from '@material-ui/icons/Delete';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import Dialog from '@material-ui/core/Dialog';
import Grid from "@material-ui/core/Grid";

interface DeleteData {
    serialNos: string[];
    setOpen: any;
    open: boolean;
}

export default function DeleteDialog(props: DeleteData) {
    const { serialNos, setOpen, open } = props;

    const handleClose = () => {
        setOpen(false);
    };

    const handleDelete = () => {
        for (var serialNo of serialNos) {
            let reqHtml = 'api/reagent/' + serialNo;
            axios.delete(reqHtml).then((res) => {
                console.log(serialNo + ' deleted!');
            })
            .catch((err) => { 
                console.log(err); 
            });
        }

        setOpen(false);
    }

    return (
        <Dialog open={open} onClose={handleClose}>
            <Grid container spacing={0} direction="column" alignItems="center" justify="center">
                <Grid item>
                    <DeleteIcon fontSize="large"/>
                </Grid>
                <Grid item>
                    <DialogTitle id="alert-dialog-slide-title">{"Delete"}</DialogTitle>
                </Grid>
                <Grid item>
                    <DialogContent>
                        <DialogContentText>
                            Are you sure you want to delete the selected {serialNos.length > 1 ? <>items?</> : <>item?</>}
                        </DialogContentText>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleClose} color="primary">
                            Cancel
                        </Button>
                        <Button onClick={handleDelete} variant="contained" color="secondary">
                            Delete
                        </Button>
                    </DialogActions>
                </Grid>
            </Grid>
        </Dialog>
    );
}