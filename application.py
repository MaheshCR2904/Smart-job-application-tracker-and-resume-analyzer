from datetime import datetime
from bson import ObjectId

class ApplicationModel:
    """Application model for job application tracking"""
    
    STATUS_CHOICES = ['Applied', 'Interview', 'Rejected', 'Offer']
    
    @staticmethod
    def create(db, user_id, data):
        """Create new job application"""
        application_data = {
            'user_id': user_id,
            'company_name': data.get('company_name'),
            'job_role': data.get('job_role'),
            'location': data.get('location'),
            'salary': data.get('salary'),
            'application_date': datetime.strptime(data.get('application_date'), '%Y-%m-%d') if data.get('application_date') else datetime.utcnow(),
            'status': data.get('status', 'Applied'),
            'notes': data.get('notes'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = db.applications.insert_one(application_data)
        application_data['_id'] = result.inserted_id
        return application_data
    
    @staticmethod
    def get_by_id(db, application_id, user_id):
        """Get application by ID"""
        try:
            return db.applications.find_one({
                '_id': ObjectId(application_id),
                'user_id': user_id
            })
        except Exception:
            return None
    
    @staticmethod
    def get_all(db, user_id, filters=None, page=1, per_page=20):
        """Get all applications for user with filters"""
        query = {'user_id': user_id}
        
        if filters:
            if filters.get('status'):
                query['status'] = filters['status']
            if filters.get('company'):
                query['company_name'] = {'$regex': filters['company'], '$options': 'i'}
            if filters.get('search'):
                query['$or'] = [
                    {'company_name': {'$regex': filters['search'], '$options': 'i'}},
                    {'job_role': {'$regex': filters['search'], '$options': 'i'}}
                ]
        
        skip = (page - 1) * per_page
        applications = list(db.applications.find(query)
                           .sort('created_at', -1)
                           .skip(skip)
                           .limit(per_page))
        
        total = db.applications.count_documents(query)
        
        return {
            'applications': applications,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    
    @staticmethod
    def update(db, application_id, user_id, data):
        """Update application"""
        try:
            update_data = {k: v for k, v in data.items() if k in [
                'company_name', 'job_role', 'location', 'salary',
                'application_date', 'status', 'notes'
            ]}
            update_data['updated_at'] = datetime.utcnow()
            
            if 'application_date' in update_data and update_data['application_date']:
                update_data['application_date'] = datetime.strptime(
                    update_data['application_date'], '%Y-%m-%d'
                )
            
            result = db.applications.update_one(
                {'_id': ObjectId(application_id), 'user_id': user_id},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    @staticmethod
    def delete(db, application_id, user_id):
        """Delete application"""
        try:
            result = db.applications.delete_one({
                '_id': ObjectId(application_id),
                'user_id': user_id
            })
            return result.deleted_count > 0
        except Exception:
            return False
    
    @staticmethod
    def get_statistics(db, user_id):
        """Get application statistics"""
        pipeline = [
            {'$match': {'user_id': user_id}},
            {'$group': {
                '_id': '$status',
                'count': {'$sum': 1}
            }}
        ]
        results = list(db.applications.aggregate(pipeline))
        
        stats = {
            'total': 0,
            'Applied': 0,
            'Interview': 0,
            'Rejected': 0,
            'Offer': 0
        }
        
        for result in results:
            stats[result['_id']] = result['count']
            stats['total'] += result['count']
        
        return stats
    
    @staticmethod
    def export_csv(db, user_id):
        """Export applications as CSV"""
        applications = list(db.applications.find({'user_id': user_id})
                          .sort('created_at', -1))
        
        csv_data = []
        for app in applications:
            # Handle application_date - could be datetime or string
            app_date = app.get('application_date')
            if app_date:
                if hasattr(app_date, 'strftime'):
                    app_date_str = app_date.strftime('%Y-%m-%d')
                else:
                    app_date_str = str(app_date)
            else:
                app_date_str = ''
            
            csv_data.append({
                'Company': app.get('company_name', ''),
                'Job Role': app.get('job_role', ''),
                'Location': app.get('location', ''),
                'Salary': app.get('salary', ''),
                'Application Date': app_date_str,
                'Status': app.get('status', ''),
                'Notes': app.get('notes', '')
            })
        
        return csv_data
