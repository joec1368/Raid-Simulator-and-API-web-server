# Simulation RAID and api server by python
* Target:
	* A RAID simulator which provides operations in HTTP.
## Detail
1. Using nginx as reverse proxy host
2. Can simulate multiple disks
3. Create a FreeBSD service to quickly start the server.
4. Implement following operateion:
	1. /api/health 
		* GET
		*  provide an endpoint that allows users to check the health of the service.
	2. /api/file
		* POST
		* Allow the users to upload a file, and use the RAID's storage method to save the file.
	3. /api/file
		* GET
		* Allow the users to retrieve previously uploaded files.
	4. /api/file
		* PUT
		* Allow the users to update previously uploaded files.
	5. /api/delete
		* DELETE
		* Enable users to delete previously uploaded files.
	6. /api/fix/<block_id:int>
		* Before accessing this endpoint,users will remove a block by giving block_id to simulate a broken data scenario. Once the error is induced, users will request the fix endpoint to restore the data, and users will ensure that the rest of the data blocks are intact.

## Start the server:
`hw4 [start | restart | stop]`

### Reference

-   [tiangolo/fastapi](https://fastapi.tiangolo.com)
-   [arashi87/FastAPI-Template](https://github.com/arasHi87/FastAPI-Template)
-   [DarkbordermanTemplate/fastapi](https://github.com/DarkbordermanTemplate/fastapi)
